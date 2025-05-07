from typing import Any, List, Optional  # noqa: F401

from ..config import config
from ..flow_metrics import KafkaMetric  # noqa: F401
from ..instrumentation.metaclass import overrideclass
from ..kafka_declaration_manager import KafkaDeclarationManager
from ..logging import internal_logger
from ..native import set_flow_id
from .base_instrumentation import BaseInstrumentation


class HudState:
    def __init__(
        self,
        topics: List[str],
        group_id: Optional[str],
        pattern: Optional[str] = None,
        metric: Optional[KafkaMetric] = None,
        const_flow_id: Optional[str] = None,
        logged: bool = False,
        is_from_anext: bool = False,
    ) -> None:
        self.kafka_declaration_manager = KafkaDeclarationManager()
        self.topics: List[str] = topics
        self.group_id: Optional[str] = group_id
        self.pattern: Optional[str] = pattern
        self.metric: Optional[KafkaMetric] = metric
        # The const flow_id is in case of pattern subscription, which can be only one pattern
        self.const_flow_id: Optional[str] = const_flow_id
        self.logged: bool = logged
        self.is_from_anext: bool = is_from_anext

    def extract_declarations(self) -> None:
        for topic in self.topics:
            self.kafka_declaration_manager.save_kafka_declaration(
                topic, self.group_id, "eachMessage"
            )
        if self.pattern:
            self.const_flow_id = self.kafka_declaration_manager.save_kafka_declaration(
                self.pattern,
                self.group_id,
                "eachMessage",
            )
        internal_logger.info(
            "extracted topics from aiokafka consumer",
            data={
                "topics": len(self.topics),
                "pattern": True if self.pattern else False,
            },
        )

    def stop_metric(self) -> None:
        if self.metric is not None:
            self.metric.stop()
            self.metric.save()
            self.metric = None


class AIOKafkaInstrumentation(BaseInstrumentation):

    def __init__(self_instrument) -> None:
        super().__init__("aiokafka", "aiokafka", "0.6.0", None)

    def is_enabled(self_instrument) -> bool:
        return config.instrument_aiokafka

    def _instrument(self_instrument) -> None:
        import aiokafka  # type: ignore[import-untyped]
        from aiokafka import TopicPartition  # noqa: F401

        class InstrumentedConsumer(aiokafka.AIOKafkaConsumer, metaclass=overrideclass(inherit_class=aiokafka.AIOKafkaConsumer)):  # type: ignore[misc]
            def __init__(self, *topics: Any, **kwargs: Any) -> None:
                super().__init__(*topics, **kwargs)
                try:
                    internal_logger.info("Instrumenting aiokafka consumer")
                    self._hud_state = HudState(
                        topics=list(topics), group_id=kwargs.get("group_id", None)
                    )
                except Exception:
                    internal_logger.exception("Error initializing aiokafka consumer")

            def subscribe(
                self,
                *args: Any,
                **kwargs: Any,
            ) -> Any:
                """
                When a user use subscribe, we save the topics/patterns in order to extract the declarations later.
                """
                result = super().subscribe(*args, **kwargs)
                try:
                    topics = args[0] if args else kwargs.get("topics", [])
                    pattern = args[1] if len(args) > 1 else kwargs.get("pattern", None)
                    self._hud_state.topics = list(topics)
                    self._hud_state.pattern = pattern
                except Exception:
                    internal_logger.exception("Error getting topics from subscribe")
                return result

            def assign(self, partitions: List[TopicPartition]) -> Any:
                """
                When a user use assign, we save the topics in order to extract the declarations later.
                """
                try:
                    self._hud_state.topics = [p.topic for p in partitions]
                except Exception:
                    internal_logger.exception("Error getting topics from partitions")
                return super().assign(partitions)

            async def start(self, *args: Any, **kwargs: Any) -> Any:
                """
                The consumer must be started before it can be used in an `async for` loop.
                We send the topics here
                """
                try:
                    self._hud_state.extract_declarations()
                except Exception:
                    internal_logger.exception("Error sending topics")
                return await super().start(*args, **kwargs)

            async def __anext__(self) -> Any:
                """
                This is the iterator method that is called when the consumer is used in an `async for` loop.
                We stop the previous metric, because we assume we are done with the processing of the previous message.
                We then start a new metric for the new message, and set the flow_id based on the topic or pattern.
                """
                try:
                    set_flow_id(None)
                    self._hud_state.stop_metric()
                    self._hud_state.is_from_anext = True
                except Exception:
                    internal_logger.exception("Error stopping metric")
                msg = await super().__anext__()
                try:
                    self._hud_state.is_from_anext = False
                    if not self._hud_state.const_flow_id:
                        flow_id = self._hud_state.kafka_declaration_manager.get_declaration_id(
                            msg.topic, self._hud_state.group_id, "eachMessage"
                        )
                    else:
                        flow_id = self._hud_state.const_flow_id
                    self._hud_state.metric = KafkaMetric(flow_id)

                    self._hud_state.metric.set_partition(msg.partition)
                    self._hud_state.metric.set_produced_timestamp(
                        getattr(msg, "timestamp", None)
                    )
                    self._hud_state.metric.start()
                    set_flow_id(flow_id)
                except Exception:
                    internal_logger.exception("Error starting metric")
                return msg

            async def getone(self, *args: Any, **kwargs: Any) -> Any:
                """
                We don't support getone in our instrumentation, so we currently log the usage of it.
                This function is called from __anext__ when the consumer is used in an `async for` loop,
                so we want to log it only if __anext__ is not called.
                """
                if not self._hud_state.is_from_anext and not self._hud_state.logged:
                    internal_logger.warning("getone used without anext")
                    self._hud_state.logged = True

                return await super().getone(*args, **kwargs)

            async def stop(self, *args: Any, **kwargs: Any) -> Any:
                """
                We need to stop the last metric when the consumer is stopped.
                """
                try:
                    self._hud_state.stop_metric()
                except Exception:
                    internal_logger.exception("Error stopping metric")
                return await super().stop(*args, **kwargs)

            async def getmany(self, *args: Any, **kwargs: Any) -> Any:
                """
                We don't support getmany in our instrumentation, so we currently log the usage of it.
                """
                try:
                    if not self._hud_state.logged:
                        internal_logger.warning("getmany used")
                        self._hud_state.logged = True
                except Exception:
                    internal_logger.exception("Error logging getmany")
                return super().getmany(*args, **kwargs)

        aiokafka.AIOKafkaConsumer = InstrumentedConsumer
