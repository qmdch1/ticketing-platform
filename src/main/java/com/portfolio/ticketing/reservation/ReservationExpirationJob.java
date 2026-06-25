package com.portfolio.ticketing.reservation;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ReservationExpirationJob {

	private final ReservationService reservationService;

	public ReservationExpirationJob(ReservationService reservationService) {
		this.reservationService = reservationService;
	}

	@Scheduled(fixedDelay = 10_000)
	public void expire() {
		reservationService.expireReservations();
	}
}
