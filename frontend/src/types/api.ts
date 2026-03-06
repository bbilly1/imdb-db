export type HttpMethod = "GET" | "POST";
export type FieldLocation = "path" | "query" | "body";
export type FieldType = "text" | "number" | "list";
export type FieldValue = string | number | string[] | undefined;
export type RenderMode = "json" | "rendered";

export interface EndpointField {
  key: string;
  label: string;
  in: FieldLocation;
  type: FieldType;
  required?: boolean;
  defaultValue?: string;
  placeholder?: string;
}

export interface EndpointConfig {
  id: string;
  title: string;
  method: HttpMethod;
  path: string;
  description: string;
  fields: EndpointField[];
}

export type EndpointFormValues = Record<string, string>;
export type FormsState = Record<string, EndpointFormValues>;

export interface EndpointResponse {
  ok: boolean;
  status: number | "client";
  url: string;
  response: unknown;
}

export type ResponsesState = Record<string, EndpointResponse>;
export type LoadingState = Record<string, boolean>;
