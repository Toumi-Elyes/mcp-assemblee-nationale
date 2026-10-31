import { HeroProof } from "./hero-proof";
import { WeekSection } from "./week-section";

export const WeekBoard: React.FC = () => {
  return (
    <div id="en-direct" className="border-t-2 border-rule pb-20 pt-14 sm:pb-24">
      <div className="mx-auto grid w-full max-w-page gap-12 px-4 sm:px-6 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <WeekSection />
        </div>
        <aside aria-label="Les votes en chiffres" className="lg:col-span-4">
          <div className="lg:sticky lg:top-6">
            <HeroProof />
          </div>
        </aside>
      </div>
    </div>
  );
};
