package com.portfolio.ticketing.order;

import java.time.Clock;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import com.portfolio.ticketing.reservation.Reservation;
import com.portfolio.ticketing.reservation.ReservationRepository;
import com.portfolio.ticketing.seat.SeatRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

	private final TicketOrderRepository orderRepository;
	private final ReservationRepository reservationRepository;
	private final SeatRepository seatRepository;
	private final Clock clock;

	public OrderService(
			TicketOrderRepository orderRepository,
			ReservationRepository reservationRepository,
			SeatRepository seatRepository,
			Clock clock) {
		this.orderRepository = orderRepository;
		this.reservationRepository = reservationRepository;
		this.seatRepository = seatRepository;
		this.clock = clock;
	}

	@Transactional
	public TicketOrder create(UUID reservationId, UUID customerId) {
		return orderRepository.findByReservationId(reservationId).orElseGet(() -> createNew(reservationId, customerId));
	}

	private TicketOrder createNew(UUID reservationId, UUID customerId) {
		Reservation reservation = reservationRepository.findByIdForUpdate(reservationId)
				.orElseThrow(() -> new BusinessException(
						HttpStatus.NOT_FOUND, "RESERVATION_NOT_FOUND", "Reservation does not exist"));
		if (!reservation.getCustomerId().equals(customerId)) {
			throw new BusinessException(HttpStatus.FORBIDDEN, "RESERVATION_OWNER_MISMATCH",
					"Reservation belongs to another customer");
		}
		reservation.ensurePurchasable(clock.instant());
		long totalAmount = seatRepository.findAllByReservationIdForUpdate(reservationId).stream()
				.mapToLong(seat -> seat.getPrice())
				.sum();
		return orderRepository.save(TicketOrder.create(reservationId, customerId, totalAmount, clock.instant()));
	}
}
