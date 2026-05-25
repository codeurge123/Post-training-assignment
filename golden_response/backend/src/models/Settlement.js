import mongoose from "mongoose";

const settlementSchema = new mongoose.Schema(
  {
    group: { type: mongoose.Schema.Types.ObjectId, ref: "Group", required: true },
    from: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    to: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    amount: { type: Number, required: true, min: 0.01 },
    status: { type: String, enum: ["pending", "completed", "failed"], default: "completed" },
    note: { type: String, trim: true, maxlength: 250, default: "" },
    recordedBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

settlementSchema.index({ group: 1, createdAt: -1 });

export default mongoose.model("Settlement", settlementSchema);
