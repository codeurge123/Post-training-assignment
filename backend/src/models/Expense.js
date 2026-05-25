import mongoose from "mongoose";

const splitSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    percentage: { type: Number, min: 0, max: 100, default: 0 },
    amount: { type: Number, min: 0, required: true }
  },
  { _id: false }
);

const expenseSchema = new mongoose.Schema(
  {
    title: { type: String, required: true, trim: true, maxlength: 120 },
    amount: { type: Number, required: true, min: 0.01 },
    category: {
      type: String,
      enum: ["Food", "Rent", "Travel", "Shopping", "Utilities", "Entertainment", "Other"],
      default: "Other"
    },
    payer: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    group: { type: mongoose.Schema.Types.ObjectId, ref: "Group", required: true },
    splitType: { type: String, enum: ["equal", "custom"], default: "equal" },
    splits: [splitSchema],
    billImage: { type: String, default: "" },
    notes: { type: String, maxlength: 500, default: "" },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

expenseSchema.index({ group: 1, createdAt: -1 });

export default mongoose.model("Expense", expenseSchema);
