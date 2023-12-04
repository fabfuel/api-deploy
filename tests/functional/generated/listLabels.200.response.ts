// THIS FILE IS GENERATED. DO NOT EDIT.


export type ListLabels200Response = {
  /**
    * _embedded
    */
  _embedded:
            {
  /**
    * label
    */
  label:
            {
  /**
    * slug
    * Example: lorem-ipsum
    */
  slug:string;
  /**
    * name
    * Example: Lorem Ipsum
    */
  name:string;
  /**
    * color
    */
  color:'red' | 'green' | 'blue';
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
  /**
    * _meta
    */
  _meta:
            {
  /**
    * count
    */
  count:number;
  /**
    * total
    */
  total:number;
  /**
    * limit
    */
  limit:number;
  /**
    * offset
    */
  offset:number;
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
};
