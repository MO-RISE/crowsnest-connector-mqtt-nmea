# brefv

A public message specification aimed at maritime usecases maintained by Maritime Operations - RISE. Its foremost usecase is to be the application layer message format for the research platform [crowsnest](https://github.com/MO-RISE/crowsnest), which utilizes MQTT as messaging protocol.

A `brefv` (swedish (old spelling) for letter) consists of an `envelope` containing a `message`. Both the `envelope` and any `message`s are ordinary JSON constructs defined through JSON schemas. The JSON schema for the `envelope` is maintained in this repository together with JSON schemas for a wide range of typical `message`s needed when dealing with the maritime domain. Note, however, that `brefv` is easily extensible with any kind of `message` and can, obviously, be applied to any domain.

The design philosophy behind `brefv` can be summarized as:
* Openness - we believe research should be open
* Ease of use - this is just standard JSON, supported by almost every programming language available
* Readability counts - human readability and development speed trumps runtime performance

## Structure

`Brefv` tries to be well-structured by dividing the message types in certain distinct groups:
* **Commands** - includes all message types used for sending commands to a remote application.
* **Core** - includes basic physical construct definitions such as position, attitude, angular velocity etc. These are generally not used as message types directly but rather as common building blocks for other, more complex, message types.
* **Observations** - is a concept introduced instead of a sensor. An observation is not bound to a specific, physical sensor, instead it may (or may not) bundle sensor readings from multiple physical sensors to create highly cohesive messages.

## Frames of reference
One of the prominent use cases of `brefv` is to exchange messages describing the motions of and observations from sensors situated onboard a rigid body. As such, `brefv` needs a well-defined way of handling data streams with different frames of reference, and the messages part of the standard message set (found in this repository) all use the following frames of reference:
* **WGS84** - used as the chart datum for all `position`s.
* **NED (North-East-Down)** - is a **non-rotating** frame of reference fixed to the geometric center of a rigid body, with the x-y plane being the tangent plane to the WGS84 ellipsoid and the z-axis points downwards towards the centre of the earth. It is used as the reference for all `attitude`s.
* **BF (Body Fixed)** - is a **rotating** frame of reference fixed to the geometric center of a rigid body, with its rotation defined as the `attitude` of the rigid body. This frame is used for the kinematic state of the vessel (i.e. linear velocity and angular velocity), any forces and moments reported by actuators or similar as well as to locate any onboard sensor equipment generating observations.

    **BF frame for marine surface vessels**

    A body-fixed frame of reference for a marine surface vessel has its axes orientated as follows:
    
    * The x-axis is parallel to the length of the vessel and positive towards the bow
    * The y-axis is parallel to the breadth of the vessel and positive towards starboard
    * The z-axis is parallel to the height of the vessel and positive towards the baseline of the hull


## License
Apache 2.0