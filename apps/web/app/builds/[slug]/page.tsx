import { collectionDetail } from "@/lib/content/pages";

const { generateStaticParams, generateMetadata, Detail } = collectionDetail("builds");
export { generateMetadata, generateStaticParams };
export default Detail;
