import Notification from "../models/Notification.js";

export const notifyUsers = async ({ users, group, type, title, message }) => {
  const uniqueUsers = [...new Set(users.map(String))];
  if (!uniqueUsers.length) return [];
  return Notification.insertMany(
    uniqueUsers.map((user) => ({
      user,
      group,
      type,
      title,
      message
    }))
  );
};
