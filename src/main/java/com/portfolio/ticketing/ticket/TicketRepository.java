package com.portfolio.ticketing.ticket;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface TicketRepository extends JpaRepository<Ticket, UUID> {

	List<Ticket> findByOrderId(UUID orderId);
}
