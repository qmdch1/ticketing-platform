package com.portfolio.ticketing.seat;

import java.util.Collection;
import java.util.List;
import java.util.UUID;

import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SeatRepository extends JpaRepository<Seat, UUID> {

	List<Seat> findByPerformanceIdOrderBySectionAscSeatNumberAsc(UUID performanceId);

	@Lock(LockModeType.PESSIMISTIC_WRITE)
	@Query("""
			select s from Seat s
			where s.performanceId = :performanceId and s.id in :seatIds
			order by s.id
			""")
	List<Seat> findAllForUpdate(
			@Param("performanceId") UUID performanceId,
			@Param("seatIds") Collection<UUID> seatIds);

	@Lock(LockModeType.PESSIMISTIC_WRITE)
	@Query("select s from Seat s where s.reservationId = :reservationId order by s.id")
	List<Seat> findAllByReservationIdForUpdate(@Param("reservationId") UUID reservationId);
}
