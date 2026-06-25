package com.portfolio.ticketing.reservation;

import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class ReservationController {

	private final ReservationService reservationService;

	public ReservationController(ReservationService reservationService) {
		this.reservationService = reservationService;
	}

	@PostMapping("/performances/{performanceId}/reservations")
	@ResponseStatus(HttpStatus.CREATED)
	ReservationResponse hold(
			@PathVariable UUID performanceId,
			@Valid @RequestBody HoldReservationRequest request) {
		return ReservationResponse.from(
				reservationService.hold(performanceId, request.customerId(), request.seatIds()));
	}

	@GetMapping("/reservations/{reservationId}")
	ReservationResponse get(@PathVariable UUID reservationId) {
		return ReservationResponse.from(reservationService.get(reservationId));
	}

	public record HoldReservationRequest(
			@NotNull UUID customerId,
			@NotEmpty List<UUID> seatIds) {
	}

	public record ReservationResponse(
			UUID id,
			UUID performanceId,
			UUID customerId,
			Set<UUID> seatIds,
			ReservationStatus status,
			Instant expiresAt) {
		static ReservationResponse from(Reservation reservation) {
			return new ReservationResponse(
					reservation.getId(),
					reservation.getPerformanceId(),
					reservation.getCustomerId(),
					reservation.getSeatIds(),
					reservation.getStatus(),
					reservation.getExpiresAt());
		}
	}
}
