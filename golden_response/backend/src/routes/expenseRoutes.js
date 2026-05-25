import { Router } from "express";
import { body } from "express-validator";
import { createExpense, deleteExpense, listExpenses, updateExpense } from "../controllers/expenseController.js";
import { protect } from "../middleware/authMiddleware.js";
import { uploadBill } from "../middleware/upload.js";
import { validate } from "../middleware/validate.js";

const router = Router();

const expenseRules = [
  body("title").trim().isLength({ min: 2 }),
  body("amount").isFloat({ min: 0.01 }),
  body("category").optional().trim(),
  body("payer").isMongoId(),
  body("group").isMongoId(),
  body("splitType").optional().isIn(["equal", "custom"])
];

router.use(protect);
router.get("/group/:groupId", listExpenses);
router.post("/", uploadBill.single("billImage"), expenseRules, validate, createExpense);
router.put("/:id", uploadBill.single("billImage"), validate, updateExpense);
router.delete("/:id", deleteExpense);

export default router;
