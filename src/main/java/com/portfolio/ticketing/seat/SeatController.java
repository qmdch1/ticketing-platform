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

	private final SeatService seatService;

	public SeatController(SeatService seatService) {
		this.seatService = seatService;
	}

	@GetMapping
	List<SeatView> seats(@PathVariable UUID performanceId) {
		return seatService.findByPerformance(performanceId);
	}
}
