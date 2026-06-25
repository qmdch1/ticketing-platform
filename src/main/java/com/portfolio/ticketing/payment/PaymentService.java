package com.portfolio.ticketing.payment;

import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import com.portfolio.ticketing.order.TicketOrder;
import com.portfolio.ticketing.order.TicketOrderRepository;
import com.portfolio.ticketing.reservation.Reservation;
import com.portfolio.ticketing.reservation.ReservationRepository;
import com.portfolio.ticketing.seat.Seat;
import com.portfolio.ticketing.seat.SeatRepository;
import com.portfolio.ticketing.ticket.Ticket;
import com.portfolio.ticketing.ticket.TicketRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PaymentService {

	private final PaymentRepository paymentRepository;
	private final TicketOrderRepository orderRepository;
	private final ReservationRepository reservationRepository;
	private final SeatRepository seatRepository;
	private final TicketRepository ticketRepository;
	private final Clock clock;

	public PaymentService(
			PaymentRepository paymentRepository,
			TicketOrderRepository orderRepository,
			ReservationRepository reservationRepository,
			SeatRepository seatRepository,
			TicketRepository ticketRepository,
			Clock clock) {
		this.paymentRepository = paymentRepository;
		this.orderRepository = orderRepository;
		this.reservationRepository = reservationRepository;
		this.seatRepository = seatRepository;
		this.ticketRepository = ticketRepository;
		this.clock = clock;
	}

	@Transactional
	public Payment approve(UUID orderId, String idempotencyKey, long amount) {
		return paymentRepository.findByIdempotencyKey(idempotencyKey)
				.map(payment -> validateReplay(payment, orderId, amount))
				.orElseGet(() -> approveNew(orderId, idempotencyKey, amount));
	}

	private Payment approveNew(UUID orderId, String idempotencyKey, long amount) {
		TicketOrder order = orderRepository.findByIdForUpdate(orderId)
				.orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "ORDER_NOT_FOUND", "Order does not exist"));
		if (order.getTotalAmount() != amount) {
			throw new BusinessException(HttpStatus.BAD_REQUEST, "PAYMENT_AMOUNT_MISMATCH", "Payment amount is incorrect");
		}

		Reservation reservation = reservationRepository.findByIdForUpdate(order.getReservationId())
				.orElseThrow(() -> new BusinessException(
						HttpStatus.NOT_FOUND, "RESERVATION_NOT_FOUND", "Reservation does not exist"));
		Instant now = clock.instant();
		reservation.confirm(now);
		order.pay();

		List<Seat> seats = seatRepository.findAllByReservationIdForUpdate(reservation.getId());
		seats.forEach(seat -> {
			seat.sell(reservation.getId());
			ticketRepository.save(Ticket.issue(order.getId(), reservation.getPerformanceId(), seat.getId(), now));
		});
		return paymentRepository.save(Payment.approved(orderId, idempotencyKey, amount, now));
	}

	private Payment validateReplay(Payment payment, UUID orderId, long amount) {
		if (!payment.getOrderId().equals(orderId) || payment.getAmount() != amount) {
			throw new BusinessException(HttpStatus.CONFLICT, "IDEMPOTENCY_KEY_REUSED",
					"Idempotency key was already used for another payment");
		}
		return payment;
	}
}
