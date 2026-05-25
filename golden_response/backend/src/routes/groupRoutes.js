import { Router } from "express";
import { body } from "express-validator";
import { addMember, createGroup, getGroup, listGroups, removeMember } from "../controllers/groupController.js";
import { protect } from "../middleware/authMiddleware.js";
import { validate } from "../middleware/validate.js";

const router = Router();

router.use(protect);
router.route("/").get(listGroups).post([body("name").trim().isLength({ min: 2 }), body("budgetLimit").optional().isNumeric()], validate, createGroup);
router.get("/:id", getGroup);
router.post("/:id/members", [body("email").isEmail().normalizeEmail()], validate, addMember);
router.delete("/:id/members/:userId", removeMember);

export default router;
