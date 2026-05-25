import User from "../models/User.js";
import { generateToken } from "../utils/token.js";

const authResponse = (user) => ({
  token: generateToken(user._id),
  user: { id: user._id, name: user.name, email: user.email, avatar: user.avatar }
});

export const register = async (req, res) => {
  const { name, email, password } = req.body;
  const existing = await User.findOne({ email });
  if (existing) return res.status(409).json({ message: "Email is already registered" });
  const user = await User.create({ name, email, password });
  res.status(201).json(authResponse(user));
};

export const login = async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select("+password");
  if (!user || !(await user.matchPassword(password))) {
    return res.status(401).json({ message: "Invalid email or password" });
  }
  res.json(authResponse(user));
};

export const profile = async (req, res) => {
  res.json({ user: { id: req.user._id, name: req.user.name, email: req.user.email, avatar: req.user.avatar } });
};
