package com.portfolio.ticketing.seat;

import java.util.UUID;

public record SeatView(UUID id, String section, String seatNumber, long price, SeatStatus status) {

	public static SeatView from(Seat seat) {
		return new SeatView(seat.getId(), seat.getSection(), seat.getSeatNumber(), seat.getPrice(), seat.getStatus());
	}
}
