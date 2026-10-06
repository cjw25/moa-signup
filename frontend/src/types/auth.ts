export type SignupFields = {
  name: string;
  email: string;
  password: string;
  password_confirmation: string;
};

export type FieldErrors = Partial<Record<keyof SignupFields, string>>;

export type SignupResult = {
  id: string;
  created_at: string;
  message: string;
};
