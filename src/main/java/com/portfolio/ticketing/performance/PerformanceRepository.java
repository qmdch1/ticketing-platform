package com.portfolio.ticketing.performance;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface PerformanceRepository extends JpaRepository<Performance, UUID> {
}
