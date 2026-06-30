"use client";
import { useRouter } from "next/navigation";
import type { Translations } from "@/lib/i18n";

type Props = {
  t: Translations;
  onClose: () => void;
};

export function UpgradeModal({ t, onClose }: Props) {
  const router = useRouter();

  const handleUpgrade = () => {
    onClose();
    router.push("/billing");
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gold rounded-xl p-6 max-w-sm w-full">
        <div className="text-3xl text-center mb-3">⭐</div>
        <h2 className="text-xl font-bold text-center text-white mb-2">
          {t.dashboard.upgradeTitle}
        </h2>
        <p className="text-gray-400 text-sm text-center mb-5">
          {t.dashboard.upgradeDesc}
        </p>
        <button
          onClick={handleUpgrade}
          className="w-full py-3 rounded-lg bg-gold text-black font-semibold hover:bg-gold-light transition-colors"
        >
          {t.dashboard.upgradeBtn}
        </button>
        <button
          onClick={onClose}
          className="w-full py-2 mt-2 text-gray-400 text-sm hover:text-white transition-colors"
        >
          {t.form.close}
        </button>
      </div>
    </div>
  );
}
