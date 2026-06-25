package com.portfolio.ticketing.order;

import java.time.Instant;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.springframework.http.HttpStatus;

@Entity
@Table(name = "ticket_orders")
public class TicketOrder {

	@Id
	private UUID id;
	private UUID reservationId;
	private UUID customerId;
	private long totalAmount;
	@Enumerated(EnumType.STRING)
	private OrderStatus status;
	private Instant createdAt;

	protected TicketOrder() {
	}

	private TicketOrder(UUID id, UUID reservationId, UUID customerId, long totalAmount, Instant createdAt) {
		this.id = id;
		this.reservationId = reservationId;
		this.customerId = customerId;
		this.totalAmount = totalAmount;
		this.status = OrderStatus.PENDING_PAYMENT;
		this.createdAt = createdAt;
	}

	public static TicketOrder create(UUID reservationId, UUID customerId, long totalAmount, Instant createdAt) {
		return new TicketOrder(UUID.randomUUID(), reservationId, customerId, totalAmount, createdAt);
	}

	public void pay() {
		if (status != OrderStatus.PENDING_PAYMENT) {
			throw new BusinessException(HttpStatus.CONFLICT, "ORDER_NOT_PAYABLE", "Order is not payable");
		}
		status = OrderStatus.PAID;
	}

	public UUID getId() {
		return id;
	}

	public UUID getReservationId() {
		return reservationId;
	}

	public UUID getCustomerId() {
		return customerId;
	}

	public long getTotalAmount() {
		return totalAmount;
	}

	public OrderStatus getStatus() {
		return status;
	}
}
