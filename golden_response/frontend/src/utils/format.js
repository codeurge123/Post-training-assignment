export const currency = (value) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);

export const shortDate = (date) => new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short" }).format(new Date(date));
