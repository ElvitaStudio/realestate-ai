import { api } from "./api";

export type ToolId =
  | "description"
  | "instagram"
  | "telegram"
  | "cold-call"
  | "incoming-call"
  | "objection"
  | "followup";

export type FieldType =
  | "select"
  | "text"
  | "textarea"
  | "number"
  | "checkbox"
  | "checkboxGroup"
  | "language";

export type FieldConfig = {
  name: string;
  labelKey: string;
  type: FieldType;
  options?: { value: string; labelKey: string }[];
  defaultValue?: unknown;
};

export type ToolConfig = {
  id: ToolId;
  icon: string;
  titleKey: string;
  descKey: string;
  fields: FieldConfig[];
  apiFn: (data: unknown) => Promise<unknown>;
};

export const TOOLS: ToolConfig[] = [
  {
    id: "description",
    icon: "🏠",
    titleKey: "tools.description",
    descKey: "tools.descriptionDesc",
    apiFn: api.generate.description,
    fields: [
      {
        name: "property_type",
        labelKey: "form.propertyType",
        type: "select",
        defaultValue: "apartment",
        options: [
          { value: "apartment", labelKey: "form.apartment" },
          { value: "house", labelKey: "form.house" },
          { value: "commercial", labelKey: "form.commercial" },
          { value: "land", labelKey: "form.land" },
        ],
      },
      { name: "rooms", labelKey: "form.rooms", type: "text", defaultValue: "" },
      { name: "floor", labelKey: "form.floor", type: "text", defaultValue: "" },
      { name: "total_floors", labelKey: "form.totalFloors", type: "text", defaultValue: "" },
      { name: "total_area", labelKey: "form.totalArea", type: "text", defaultValue: "" },
      { name: "living_area", labelKey: "form.livingArea", type: "text", defaultValue: "" },
      { name: "kitchen_area", labelKey: "form.kitchenArea", type: "text", defaultValue: "" },
      { name: "district", labelKey: "form.district", type: "text", defaultValue: "" },
      { name: "city", labelKey: "form.city", type: "text", defaultValue: "" },
      {
        name: "condition",
        labelKey: "form.condition",
        type: "select",
        defaultValue: "euro",
        options: [
          { value: "euro", labelKey: "form.euro" },
          { value: "cosmetic", labelKey: "form.cosmetic" },
          { value: "no_repair", labelKey: "form.noRepair" },
          { value: "new_building", labelKey: "form.newBuilding" },
        ],
      },
      {
        name: "features",
        labelKey: "form.features",
        type: "checkboxGroup",
        defaultValue: [],
        options: [
          { value: "balcony", labelKey: "form.balcony" },
          { value: "parking", labelKey: "form.parking" },
          { value: "closed_yard", labelKey: "form.closedYard" },
          { value: "concierge", labelKey: "form.concierge" },
          { value: "new_house", labelKey: "form.newHouse" },
          { value: "panoramic_view", labelKey: "form.panoramicView" },
          { value: "near_metro", labelKey: "form.nearMetro" },
          { value: "quiet_yard", labelKey: "form.quietYard" },
        ],
      },
      { name: "additional", labelKey: "form.additional", type: "textarea", defaultValue: "" },
    ],
  },
  {
    id: "instagram",
    icon: "📸",
    titleKey: "tools.instagram",
    descKey: "tools.instagramDesc",
    apiFn: api.generate.instagram,
    fields: [
      { name: "property_description", labelKey: "form.propertyDesc", type: "textarea", defaultValue: "" },
      {
        name: "tone",
        labelKey: "form.tone",
        type: "select",
        defaultValue: "emotional",
        options: [
          { value: "emotional", labelKey: "form.emotional" },
          { value: "business", labelKey: "form.business" },
          { value: "premium", labelKey: "form.premium" },
        ],
      },
      { name: "use_emoji", labelKey: "form.useEmoji", type: "checkbox", defaultValue: true },
    ],
  },
  {
    id: "telegram",
    icon: "✈️",
    titleKey: "tools.telegram",
    descKey: "tools.telegramDesc",
    apiFn: api.generate.telegram,
    fields: [
      { name: "property_description", labelKey: "form.propertyDesc", type: "textarea", defaultValue: "" },
      {
        name: "tone",
        labelKey: "form.tone",
        type: "select",
        defaultValue: "selling",
        options: [
          { value: "informative", labelKey: "form.informative" },
          { value: "selling", labelKey: "form.selling" },
        ],
      },
    ],
  },
  {
    id: "cold-call",
    icon: "📞",
    titleKey: "tools.coldCall",
    descKey: "tools.coldCallDesc",
    apiFn: api.generate.coldCall,
    fields: [
      {
        name: "goal",
        labelKey: "form.callGoal",
        type: "select",
        defaultValue: "sell_property",
        options: [
          { value: "sell_property", labelKey: "form.sellProperty" },
          { value: "find_seller", labelKey: "form.findSeller" },
          { value: "evaluation", labelKey: "form.evaluation" },
        ],
      },
      {
        name: "client_type",
        labelKey: "form.clientType",
        type: "select",
        defaultValue: "buyer",
        options: [
          { value: "owner", labelKey: "form.owner" },
          { value: "buyer", labelKey: "form.buyer" },
          { value: "investor", labelKey: "form.investor" },
        ],
      },
    ],
  },
  {
    id: "incoming-call",
    icon: "📲",
    titleKey: "tools.incomingCall",
    descKey: "tools.incomingCallDesc",
    apiFn: api.generate.incomingCall,
    fields: [
      {
        name: "property_type",
        labelKey: "form.propertyType",
        type: "select",
        defaultValue: "apartment",
        options: [
          { value: "apartment", labelKey: "form.apartment" },
          { value: "house", labelKey: "form.house" },
          { value: "commercial", labelKey: "form.commercial" },
          { value: "land", labelKey: "form.land" },
        ],
      },
    ],
  },
  {
    id: "objection",
    icon: "🛡️",
    titleKey: "tools.objection",
    descKey: "tools.objectionDesc",
    apiFn: api.generate.objection,
    fields: [
      {
        name: "objection",
        labelKey: "form.objection",
        type: "select",
        defaultValue: "expensive",
        options: [
          { value: "expensive", labelKey: "form.expensive" },
          { value: "think", labelKey: "form.think" },
          { value: "comparing", labelKey: "form.comparing" },
          { value: "bad_location", labelKey: "form.badLocation" },
          { value: "discount", labelKey: "form.discount" },
          { value: "custom", labelKey: "form.custom" },
        ],
      },
      { name: "custom_objection", labelKey: "form.customObjection", type: "text", defaultValue: "" },
    ],
  },
  {
    id: "followup",
    icon: "💬",
    titleKey: "tools.followup",
    descKey: "tools.followupDesc",
    apiFn: api.generate.followup,
    fields: [
      {
        name: "viewing_result",
        labelKey: "form.viewingResult",
        type: "select",
        defaultValue: "thinking",
        options: [
          { value: "liked", labelKey: "form.liked" },
          { value: "disliked", labelKey: "form.disliked" },
          { value: "thinking", labelKey: "form.thinking" },
        ],
      },
      { name: "client_feedback", labelKey: "form.clientFeedback", type: "textarea", defaultValue: "" },
    ],
  },
];
