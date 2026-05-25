export const roundMoney = (value) => Math.round((Number(value) + Number.EPSILON) * 100) / 100;

export const assertPercentTotal = (splits) => {
  const total = roundMoney(splits.reduce((sum, split) => sum + Number(split.percentage || 0), 0));
  return Math.abs(total - 100) <= 0.01;
};
