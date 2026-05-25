import { Router } from "express";
import { body } from "express-validator";
import { getSettlementSummary, recordPayment, sendReminder } from "../controllers/settlementController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.use(protect);
router.get("/:groupId", getSettlementSummary);
router.post(
  "/pay",
  [body("group").isMongoId(), body("from").isMongoId(), body("to").isMongoId(), body("amount").isFloat({ min: 0.01 })],
  validate,
  recordPayment
);
router.post("/remind", [body("group").isMongoId(), body("to").isMongoId()], validate, sendReminder);

export default router;
