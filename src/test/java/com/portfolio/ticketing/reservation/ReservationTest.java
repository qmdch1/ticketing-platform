package com.portfolio.ticketing.reservation;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;
import java.util.Set;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import org.junit.jupiter.api.Test;

class ReservationTest {

	private static final Instant NOW = Instant.parse("2026-06-25T00:00:00Z");

	@Test
	void confirmsAnActiveReservation() {
		Reservation reservation = reservation(NOW.plusSeconds(300));

		reservation.confirm(NOW);

		assertThat(reservation.getStatus()).isEqualTo(ReservationStatus.CONFIRMED);
	}

	@Test
	void rejectsPaymentAtTheExactExpirationTime() {
		Reservation reservation = reservation(NOW);

		assertThatThrownBy(() -> reservation.confirm(NOW))
				.isInstanceOf(BusinessException.class)
				.hasMessageContaining("expired");
	}

	@Test
	void expiresAHeldReservation() {
		Reservation reservation = reservation(NOW.minusSeconds(1));

		reservation.expire(NOW);

		assertThat(reservation.getStatus()).isEqualTo(ReservationStatus.EXPIRED);
	}

	private Reservation reservation(Instant expiresAt) {
		return Reservation.hold(
				UUID.randomUUID(),
				UUID.randomUUID(),
				UUID.randomUUID(),
				Set.of(UUID.randomUUID()),
				NOW.minusSeconds(60),
				expiresAt);
	}
}
