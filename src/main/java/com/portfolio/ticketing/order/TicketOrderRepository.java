package com.portfolio.ticketing.order;

import java.util.Optional;
import java.util.UUID;

import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface TicketOrderRepository extends JpaRepository<TicketOrder, UUID> {

	Optional<TicketOrder> findByReservationId(UUID reservationId);

	@Lock(LockModeType.PESSIMISTIC_WRITE)
	@Query("select o from TicketOrder o where o.id = :id")
	Optional<TicketOrder> findByIdForUpdate(@Param("id") UUID id);
}
