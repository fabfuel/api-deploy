// THIS FILE IS GENERATED. DO NOT EDIT.


export type Ping200Response = {
  /**
    * ping
    * Example: pong
    */
  ping:string;
  /**
    * pingBy
    * Example: user@server.com
    */
  pingBy:string;
  /**
    * pingAt
    */
  pingAt:string;
  /**
    * locations
    */
  locations:string[];
  /**
    * category
    */
  category:null | 'machine' | 'human' | 'other';
  /**
    * priority
    */
  priority:0 | 10 | 20 | 30 | 40;
};
