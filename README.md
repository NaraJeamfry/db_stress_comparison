# DB stress comparison for Cosplaye.rs

I'm currently building a new application to serve as a social network to cosplayers. As such, users will be able to
interact between them in multiple ways, like:

* Upload and manage pictures
* Tagging pictures with defined tags (that are searchable, and users can follow directly)
* Like, comment or otherwise interact with specific pictures
* Perform pretty complicated queries to all this data, for example:
    - Retrieve a list of pictures that share tags with a given picture, sorted by the count of tags a user follows
    - Retrieve a list of tags considered similar to the tags currently followed by the user, taking into account the
      list of pictures liked by the user and the tags of these pictures

These queries will **probably** be too much for a relational database, but theory says a graph DB will be really
powerful in the sense of making these calculations fast enough. Additionally, databases like Dgraph provide ACID
compliance and use minimal resources, so they should be safe to use for these use-cases.

So, I wanted to make sure what database I actually will use. To do so, I want to compare the performance of each
DB paradigm in some example and edge cases.

## How to build

TBD

## Example schema (in GraphQL)

```graphql
type User {
    username: String
    uuid: String! @id
    uploadedPictures: [Picture!]
    likedPictures: [Picture!]
}

type Tag {
    name: String
    uuid: String! @id
    relatedTags: [Tag!]
    taggedPictures: [Picture!]
}

type Picture {
    title: String
    uuid: String! @id
    isAbout: [Tag!] @hasInverse(field: "taggedPictures")
    uploader: User! @hasInverse(field: "uploadedPictures")
    likedBy: [User!] @hasInverse(field: "likedPictures")
}
```

