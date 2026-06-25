package com.portfolio.ticketing.reservation;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import com.portfolio.ticketing.performance.PerformanceRepository;
import com.portfolio.ticketing.seat.Seat;
import com.portfolio.ticketing.seat.SeatRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ReservationService {

	private final ReservationRepository reservationRepository;
	private final PerformanceRepository performanceRepository;
	private final SeatRepository seatRepository;
	private final Clock clock;
	private final Duration holdDuration;

	public ReservationService(
			ReservationRepository reservationRepository,
			PerformanceRepository performanceRepository,
			SeatRepository seatRepository,
			Clock clock,
			@Value("${ticketing.reservation.hold-duration}") Duration holdDuration) {
		this.reservationRepository = reservationRepository;
		this.performanceRepository = performanceRepository;
		this.seatRepository = seatRepository;
		this.clock = clock;
		this.holdDuration = holdDuration;
	}

	@Transactional
	public Reservation hold(UUID performanceId, UUID customerId, List<UUID> requestedSeatIds) {
		if (requestedSeatIds == null || requestedSeatIds.isEmpty()) {
			throw new BusinessException(HttpStatus.BAD_REQUEST, "SEAT_REQUIRED", "At least one seat is required");
		}
		if (!performanceRepository.existsById(performanceId)) {
			throw new BusinessException(HttpStatus.NOT_FOUND, "PERFORMANCE_NOT_FOUND", "Performance does not exist");
		}

		var seatIds = new LinkedHashSet<>(requestedSeatIds);
		List<Seat> seats = seatRepository.findAllForUpdate(performanceId, seatIds);
		if (seats.size() != seatIds.size()) {
			throw new BusinessException(HttpStatus.BAD_REQUEST, "INVALID_SEAT", "Some seats do not belong to the performance");
		}

		UUID reservationId = UUID.randomUUID();
		Instant now = clock.instant();
		Reservation reservation = Reservation.hold(
				reservationId, performanceId, customerId, seatIds, now, now.plus(holdDuration));
		seats.forEach(seat -> seat.hold(reservationId));
		return reservationRepository.save(reservation);
	}

	@Transactional(readOnly = true)
	public Reservation get(UUID reservationId) {
		return reservationRepository.findById(reservationId)
				.orElseThrow(() -> new BusinessException(
						HttpStatus.NOT_FOUND, "RESERVATION_NOT_FOUND", "Reservation does not exist"));
	}

	@Transactional
	public int expireReservations() {
		Instant now = clock.instant();
		List<Reservation> expired = reservationRepository
				.findTop100ByStatusAndExpiresAtLessThanEqualOrderByExpiresAtAsc(ReservationStatus.HELD, now);
		expired.forEach(reservation -> {
			seatRepository.findAllByReservationIdForUpdate(reservation.getId())
					.forEach(seat -> seat.release(reservation.getId()));
			reservation.expire(now);
		});
		return expired.size();
	}
}
