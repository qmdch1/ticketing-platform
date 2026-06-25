package com.portfolio.ticketing.reservation;

import java.time.Instant;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Table;
import org.springframework.http.HttpStatus;

@Entity
@Table(name = "reservations")
public class Reservation {

	@Id
	private UUID id;
	private UUID performanceId;
	private UUID customerId;
	@Enumerated(EnumType.STRING)
	private ReservationStatus status;
	private Instant expiresAt;
	private Instant createdAt;
	@ElementCollection(fetch = FetchType.EAGER)
	@CollectionTable(name = "reservation_seats", joinColumns = @JoinColumn(name = "reservation_id"))
	@Column(name = "seat_id")
	private Set<UUID> seatIds = new LinkedHashSet<>();

	protected Reservation() {
	}

	private Reservation(UUID id, UUID performanceId, UUID customerId, Set<UUID> seatIds, Instant now, Instant expiresAt) {
		this.id = id;
		this.performanceId = performanceId;
		this.customerId = customerId;
		this.seatIds = new LinkedHashSet<>(seatIds);
		this.status = ReservationStatus.HELD;
		this.createdAt = now;
		this.expiresAt = expiresAt;
	}

	public static Reservation hold(
			UUID id, UUID performanceId, UUID customerId, Set<UUID> seatIds, Instant now, Instant expiresAt) {
		if (seatIds.isEmpty()) {
			throw new IllegalArgumentException("At least one seat is required");
		}
		return new Reservation(id, performanceId, customerId, seatIds, now, expiresAt);
	}

	public void ensurePurchasable(Instant now) {
		if (status != ReservationStatus.HELD || !now.isBefore(expiresAt)) {
			throw new BusinessException(HttpStatus.CONFLICT, "RESERVATION_NOT_PURCHASABLE",
					"Reservation is not active or has expired");
		}
	}

	public void confirm(Instant now) {
		ensurePurchasable(now);
		status = ReservationStatus.CONFIRMED;
	}

	public void expire(Instant now) {
		if (status == ReservationStatus.HELD && !now.isBefore(expiresAt)) {
			status = ReservationStatus.EXPIRED;
		}
	}

	public UUID getId() {
		return id;
	}

	public UUID getPerformanceId() {
		return performanceId;
	}

	public UUID getCustomerId() {
		return customerId;
	}

	public ReservationStatus getStatus() {
		return status;
	}

	public Instant getExpiresAt() {
		return expiresAt;
	}

	public Set<UUID> getSeatIds() {
		return Set.copyOf(seatIds);
	}
}
