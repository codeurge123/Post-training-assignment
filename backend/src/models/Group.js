import mongoose from "mongoose";

const memberSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    role: { type: String, enum: ["owner", "member"], default: "member" },
    joinedAt: { type: Date, default: Date.now }
  },
  { _id: false }
);

const groupSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true, maxlength: 100 },
    description: { type: String, trim: true, maxlength: 300, default: "" },
    type: { type: String, enum: ["Trip", "Flat", "Outing", "Other"], default: "Other" },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    members: [memberSchema],
    budgetLimit: { type: Number, default: 0, min: 0 }
  },
  { timestamps: true }
);

groupSchema.index({ "members.user": 1 });

export default mongoose.model("Group", groupSchema);
