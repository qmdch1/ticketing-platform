package com.portfolio.ticketing.ticket;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "tickets")
public class Ticket {

	@Id
	private UUID id;
	private UUID orderId;
	private UUID performanceId;
	private UUID seatId;
	private String ticketCode;
	@Enumerated(EnumType.STRING)
	private TicketStatus status;
	private Instant issuedAt;

	protected Ticket() {
	}

	private Ticket(UUID orderId, UUID performanceId, UUID seatId, Instant issuedAt) {
		this.id = UUID.randomUUID();
		this.orderId = orderId;
		this.performanceId = performanceId;
		this.seatId = seatId;
		this.ticketCode = UUID.randomUUID().toString();
		this.status = TicketStatus.ISSUED;
		this.issuedAt = issuedAt;
	}

	public static Ticket issue(UUID orderId, UUID performanceId, UUID seatId, Instant issuedAt) {
		return new Ticket(orderId, performanceId, seatId, issuedAt);
	}

	public UUID getId() {
		return id;
	}

	public UUID getOrderId() {
		return orderId;
	}

	public UUID getPerformanceId() {
		return performanceId;
	}

	public UUID getSeatId() {
		return seatId;
	}

	public String getTicketCode() {
		return ticketCode;
	}

	public Instant getIssuedAt() {
		return issuedAt;
	}
}
