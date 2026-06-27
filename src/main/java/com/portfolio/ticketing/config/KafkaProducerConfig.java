package com.portfolio.ticketing.config;

import java.util.HashMap;
import java.util.Map;

import com.portfolio.ticketing.ticket.TicketIssuedEvent;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.support.serializer.JacksonJsonSerializer;

@Configuration
public class KafkaProducerConfig {

	@Bean
	ProducerFactory<String, TicketIssuedEvent> ticketIssuedProducerFactory(
			@Value("${spring.kafka.bootstrap-servers}") String bootstrapServers) {
		Map<String, Object> config = new HashMap<>();
		config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
		config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
		config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JacksonJsonSerializer.class);
		config.put(JacksonJsonSerializer.ADD_TYPE_INFO_HEADERS, false);
		return new DefaultKafkaProducerFactory<>(config);
	}

	@Bean
	KafkaTemplate<String, TicketIssuedEvent> ticketIssuedKafkaTemplate(
			ProducerFactory<String, TicketIssuedEvent> producerFactory) {
		return new KafkaTemplate<>(producerFactory);
	}
}
