import { Router } from "express";
import { body } from "express-validator";
import { login, profile, register } from "../controllers/authController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.post(
  "/register",
  [body("name").trim().isLength({ min: 2 }), body("email").isEmail().normalizeEmail(), body("password").isLength({ min: 6 })],
  validate,
  register
);
router.post("/login", [body("email").isEmail().normalizeEmail(), body("password").notEmpty()], validate, login);
router.get("/profile", protect, profile);

export default router;
