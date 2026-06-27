package com.portfolio.ticketing.seat;

import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class SeatService {

	private final SeatRepository seatRepository;
	private final SeatCacheService seatCacheService;

	public SeatService(SeatRepository seatRepository, SeatCacheService seatCacheService) {
		this.seatRepository = seatRepository;
		this.seatCacheService = seatCacheService;
	}

	@Transactional(readOnly = true)
	public List<SeatView> findByPerformance(UUID performanceId) {
		List<SeatView> cached = seatCacheService.get(performanceId);
		if (!cached.isEmpty()) {
			return cached;
		}
		List<SeatView> seats = seatRepository.findByPerformanceIdOrderBySectionAscSeatNumberAsc(performanceId).stream()
				.map(SeatView::from)
				.toList();
		seatCacheService.put(performanceId, seats);
		return seats;
	}
}
