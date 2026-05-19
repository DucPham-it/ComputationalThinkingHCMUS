const VI_NUMBER_FORMAT = new Intl.NumberFormat("vi-VN", {
  maximumFractionDigits: 1,
  minimumFractionDigits: 0,
});

export function formatDistanceVi(meters) {
  if (meters === null || meters === undefined || Number.isNaN(Number(meters))) {
    return "";
  }

  const value = Number(meters);
  if (value < 1000) {
    return `${Math.round(value)} m`;
  }

  const kilometers = value / 1000;
  const formatted = VI_NUMBER_FORMAT.format(kilometers).replace(",", ",");
  return `${formatted} km`;
}

export function formatDurationVi(seconds) {
  if (seconds === null || seconds === undefined || Number.isNaN(Number(seconds))) {
    return "";
  }

  const totalSeconds = Math.max(0, Math.round(Number(seconds)));
  const totalMinutes = Math.max(1, Math.round(totalSeconds / 60));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours === 0) {
    return `${minutes} phút`;
  }

  if (minutes === 0) {
    return `${hours} giờ`;
  }

  return `${hours} giờ ${minutes} phút`;
}

export function formatETA(dateInput) {
  if (!dateInput) {
    return "";
  }

  const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

export function formatRemainingText(distanceMetersOrText, durationSecondsOrText) {
  const distanceText =
    typeof distanceMetersOrText === "number"
      ? formatDistanceVi(distanceMetersOrText)
      : distanceMetersOrText || "";

  const durationText =
    typeof durationSecondsOrText === "number"
      ? formatDurationVi(durationSecondsOrText)
      : durationSecondsOrText || "";

  if (!distanceText && !durationText) {
    return "";
  }

  if (!distanceText) {
    return durationText;
  }

  if (!durationText) {
    return distanceText;
  }

  return `Còn ${distanceText} · ${durationText}`;
}
