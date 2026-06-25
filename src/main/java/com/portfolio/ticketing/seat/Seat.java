package com.portfolio.ticketing.seat;

import java.util.UUID;

import com.portfolio.ticketing.common.BusinessException;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import org.springframework.http.HttpStatus;

@Entity
@Table(name = "seats")
public class Seat {

	@Id
	private UUID id;
	private UUID performanceId;
	private String section;
	private String seatNumber;
	private long price;
	@Enumerated(EnumType.STRING)
	private SeatStatus status;
	private UUID reservationId;
	@Version
	private long version;

	protected Seat() {
	}

	public void hold(UUID reservationId) {
		if (status != SeatStatus.AVAILABLE) {
			throw new BusinessException(HttpStatus.CONFLICT, "SEAT_NOT_AVAILABLE",
					"Seat %s is not available".formatted(id));
		}
		this.status = SeatStatus.HELD;
		this.reservationId = reservationId;
	}

	public void release(UUID reservationId) {
		if (status == SeatStatus.HELD && reservationId.equals(this.reservationId)) {
			this.status = SeatStatus.AVAILABLE;
			this.reservationId = null;
		}
	}

	public void sell(UUID reservationId) {
		if (status != SeatStatus.HELD || !reservationId.equals(this.reservationId)) {
			throw new BusinessException(HttpStatus.CONFLICT, "INVALID_SEAT_STATE",
					"Seat %s is not held by this reservation".formatted(id));
		}
		this.status = SeatStatus.SOLD;
	}

	public UUID getId() {
		return id;
	}

	public UUID getPerformanceId() {
		return performanceId;
	}

	public String getSection() {
		return section;
	}

	public String getSeatNumber() {
		return seatNumber;
	}

	public long getPrice() {
		return price;
	}

	public SeatStatus getStatus() {
		return status;
	}
}
