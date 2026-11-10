import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("log");
export { generateMetadata, generateStaticParams };
export default Detail;
