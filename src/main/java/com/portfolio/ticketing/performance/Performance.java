package com.portfolio.ticketing.performance;

import java.time.Instant;
import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "performances")
public class Performance {

	@Id
	private UUID id;
	private String title;
	private Instant startsAt;

	protected Performance() {
	}

	public UUID getId() {
		return id;
	}

	public String getTitle() {
		return title;
	}

	public Instant getStartsAt() {
		return startsAt;
	}
}
