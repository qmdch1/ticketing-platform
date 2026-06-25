package com.portfolio.ticketing.payment;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "payments")
public class Payment {

	@Id
	private UUID id;
	private UUID orderId;
	private String idempotencyKey;
	private long amount;
	@Enumerated(EnumType.STRING)
	private PaymentStatus status;
	private Instant approvedAt;

	protected Payment() {
	}

	private Payment(UUID orderId, String idempotencyKey, long amount, Instant approvedAt) {
		this.id = UUID.randomUUID();
		this.orderId = orderId;
		this.idempotencyKey = idempotencyKey;
		this.amount = amount;
		this.status = PaymentStatus.APPROVED;
		this.approvedAt = approvedAt;
	}

	public static Payment approved(UUID orderId, String idempotencyKey, long amount, Instant approvedAt) {
		return new Payment(orderId, idempotencyKey, amount, approvedAt);
	}

	public UUID getId() {
		return id;
	}

	public UUID getOrderId() {
		return orderId;
	}

	public long getAmount() {
		return amount;
	}

	public PaymentStatus getStatus() {
		return status;
	}

	public Instant getApprovedAt() {
		return approvedAt;
	}
}
