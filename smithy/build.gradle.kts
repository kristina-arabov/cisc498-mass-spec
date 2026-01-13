plugins {
    `java-library`
    id("software.amazon.smithy.gradle.smithy-jar") version "1.3.0"
}

repositories {
    mavenLocal()
    mavenCentral()
}

dependencies {
    smithyBuild("software.amazon.smithy.docgen:smithy-docgen-core:0.1.0")
}
