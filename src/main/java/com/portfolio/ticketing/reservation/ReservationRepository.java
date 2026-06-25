package com.portfolio.ticketing.reservation;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface ReservationRepository extends JpaRepository<Reservation, UUID> {

	@Lock(LockModeType.PESSIMISTIC_WRITE)
	@Query("select r from Reservation r where r.id = :id")
	java.util.Optional<Reservation> findByIdForUpdate(@Param("id") UUID id);

	List<Reservation> findTop100ByStatusAndExpiresAtLessThanEqualOrderByExpiresAtAsc(
			ReservationStatus status, Instant expiresAt);
}
