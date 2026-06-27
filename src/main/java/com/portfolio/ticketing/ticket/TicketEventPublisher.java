package com.portfolio.ticketing.ticket;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

@Component
public class TicketEventPublisher {

	private final KafkaTemplate<String, TicketIssuedEvent> kafkaTemplate;
	private final String topic;

	public TicketEventPublisher(
			KafkaTemplate<String, TicketIssuedEvent> kafkaTemplate,
			@Value("${ticketing.kafka.ticket-issued-topic}") String topic) {
		this.kafkaTemplate = kafkaTemplate;
		this.topic = topic;
	}

	public void publishAfterCommit(TicketIssuedEvent event) {
		if (!TransactionSynchronizationManager.isSynchronizationActive()) {
			publish(event);
			return;
		}
		TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
			@Override
			public void afterCommit() {
				publish(event);
			}
		});
	}

	private void publish(TicketIssuedEvent event) {
		kafkaTemplate.send(topic, event.ticketId().toString(), event);
	}
}
