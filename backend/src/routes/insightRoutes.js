import { Router } from "express";
import { getInsights } from "../controllers/insightController.js";
import { protect } from "../middleware/authMiddleware.js";

const router = Router();

router.use(protect);
router.get("/:groupId", getInsights);

export default router;
