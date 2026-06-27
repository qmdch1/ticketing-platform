package com.portfolio.ticketing.ticket;

import java.time.Instant;
import java.util.UUID;

public record TicketIssuedEvent(
		UUID ticketId,
		UUID orderId,
		UUID performanceId,
		UUID seatId,
		String ticketCode,
		Instant issuedAt) {

	public static TicketIssuedEvent from(Ticket ticket) {
		return new TicketIssuedEvent(
				ticket.getId(),
				ticket.getOrderId(),
				ticket.getPerformanceId(),
				ticket.getSeatId(),
				ticket.getTicketCode(),
				ticket.getIssuedAt());
	}
}
