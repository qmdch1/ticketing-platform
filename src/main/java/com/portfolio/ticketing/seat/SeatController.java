package com.portfolio.ticketing.seat;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/performances/{performanceId}/seats")
public class SeatController {

	private final SeatRepository seatRepository;

	public SeatController(SeatRepository seatRepository) {
		this.seatRepository = seatRepository;
	}

	@GetMapping
	List<SeatResponse> seats(@PathVariable UUID performanceId) {
		return seatRepository.findByPerformanceIdOrderBySectionAscSeatNumberAsc(performanceId).stream()
				.map(SeatResponse::from)
				.toList();
	}

	record SeatResponse(UUID id, String section, String seatNumber, long price, SeatStatus status) {
		static SeatResponse from(Seat seat) {
			return new SeatResponse(seat.getId(), seat.getSection(), seat.getSeatNumber(), seat.getPrice(), seat.getStatus());
		}
	}
}
