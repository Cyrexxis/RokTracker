import type { ValidationRule } from 'quasar'

export const notEmptyRule = [(val: string | undefined) => !!val || 'Required'] as ValidationRule[]

export const notEmptyArrayRule = [
  (val: unknown[] | undefined) => (val !== undefined && val.length > 0) || 'Required',
] as ValidationRule[]

export const intRule = [
  ...notEmptyRule,
  (val: string | undefined) =>
    Number.isInteger(Number(val)) || 'Please enter a number without decimals',
] as ValidationRule[]

export const floatRule = [
  ...notEmptyRule,
  (val: string | undefined) => Number.isNaN(Number(val)) == false || 'Please enter a number',
] as ValidationRule[]
