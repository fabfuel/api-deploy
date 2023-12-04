// THIS FILE IS GENERATED. DO NOT EDIT.


export type GetOffer200Response = {
  /**
    * offerId
    */
  offerId:string;
  /**
    * projectId
    */
  projectId:string;
  /**
    * vendorId
    */
  vendorId:string;
  /**
    * attachments
    */
  attachments:
            {
  /**
    * name
    * Example: example.pdf
    */
  name:string;
  /**
    * path
    * Example: /vendors/1234567890/some.pdf
    */
  path:string;
  /**
    * uploadedAt
    */
  uploadedAt:string;
  /**
    * uploadedBy
    */
  uploadedBy:string;
}[];
  /**
    * comment
    * Example: User generated info about the offer
    */
  comment:string | null;
  /**
    * state
    */
  state:'draft' | 'submitted';
  /**
    * stateTransitions
    */
  stateTransitions:
            {
  /**
    * originalState
    * Example: state1
    */
  originalState:string;
  /**
    * targetState
    * Example: state2
    */
  targetState:string;
  /**
    * transitionedAt
    */
  transitionedAt:string;
  /**
    * transitionedBy
    */
  transitionedBy:string;
  /**
    * comment
    * Example: Additional user generated info about the transition
    */
  comment:string | null;
}[];
  /**
    * _meta
    */
  _meta:
            {
  /**
    * createdAt
    */
  createdAt:string | null;
  /**
    * createdBy
    */
  createdBy:string;
  /**
    * modifiedAt
    */
  modifiedAt:string | null;
  /**
    * modifiedBy
    */
  modifiedBy:string;
  /**
    * revisionedAt
    */
  revisionedAt:string | null;
  /**
    * revisionedBy
    */
  revisionedBy:string;
  /**
    * archivedAt
    */
  archivedAt:string | null;
  /**
    * archivedBy
    */
  archivedBy:string;
  /**
    * _links
    */
  _links:
            {
  /**
    * self
    */
  self?:
            {
  /**
    * href
    * Example: https://api.server.com/v1/projects/5d4470a6-121b-40d2-aff9-00f24aa4a110
    */
  href:string;
};
};
};
  /**
    * _links
    */
  _links:
            {
  /**
    * self
    */
  self?:
            {
  /**
    * href
    * Example: https://api.server.com/v1/projects/5d4470a6-121b-40d2-aff9-00f24aa4a110
    */
  href:string;
};
};
  /**
    * _embedded
    */
  _embedded:
            {
  /**
    * project
    */
  project:
            {
  /**
    * projectId
    */
  projectId:string;
  /**
    * customerId
    */
  customerId:string;
  /**
    * attachments
    */
  attachments:
            {
  /**
    * name
    * Example: example.pdf
    */
  name:string;
  /**
    * path
    * Example: /vendors/1234567890/some.pdf
    */
  path:string;
  /**
    * uploadedAt
    */
  uploadedAt:string;
  /**
    * uploadedBy
    */
  uploadedBy:string;
}[];
  /**
    * company
    */
  company:
            {
  /**
    * name
    * Example: Company AY
    */
  name:string;
  /**
    * email
    * Example: mail@server.com
    */
  email:string;
  /**
    * phoneNumber
    * Example: +49 (30) 1234567890
    */
  phoneNumber:string | null;
  /**
    * deliveryAddress
    */
  deliveryAddress:
            {
  /**
    * streetAddress
    * Example: My Street 123
    */
  streetAddress:string | null;
  /**
    * postalCode
    * Example: 10119
    */
  postalCode:string;
  /**
    * locality
    * Example: Berlin
    */
  locality:string | null;
  /**
    * region
    * Example: Berlin
    */
  region:string | null;
  /**
    * country
    * Example: de
    */
  country:string;
};
};
  /**
    * description
    * Example: This is an example project
    */
  description:string | null;
  /**
    * title
    * Example: Example project
    */
  title:string;
  /**
    * state
    */
  state:'new' | 'active' | 'done';
  /**
    * stateTransitions
    */
  stateTransitions:
            {
  /**
    * originalState
    * Example: state1
    */
  originalState:string;
  /**
    * targetState
    * Example: state2
    */
  targetState:string;
  /**
    * transitionedAt
    */
  transitionedAt:string;
  /**
    * transitionedBy
    */
  transitionedBy:string;
  /**
    * comment
    * Example: Additional user generated info about the transition
    */
  comment:string | null;
}[];
  /**
    * _meta
    */
  _meta:
            {
  /**
    * createdAt
    */
  createdAt:string | null;
  /**
    * createdBy
    */
  createdBy:string;
  /**
    * modifiedAt
    */
  modifiedAt:string | null;
  /**
    * modifiedBy
    */
  modifiedBy:string;
  /**
    * revisionedAt
    */
  revisionedAt:string | null;
  /**
    * revisionedBy
    */
  revisionedBy:string;
  /**
    * archivedAt
    */
  archivedAt:string | null;
  /**
    * archivedBy
    */
  archivedBy:string;
  /**
    * _links
    */
  _links:
            {
  /**
    * self
    */
  self?:
            {
  /**
    * href
    * Example: https://api.server.com/v1/projects/5d4470a6-121b-40d2-aff9-00f24aa4a110
    */
  href:string;
};
};
};
  /**
    * _links
    */
  _links:
            {
  /**
    * self
    */
  self?:
            {
  /**
    * href
    * Example: https://api.server.com/v1/projects/5d4470a6-121b-40d2-aff9-00f24aa4a110
    */
  href:string;
};
};
}[];
};
};
