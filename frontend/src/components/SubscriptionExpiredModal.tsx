"use client";

type Props = {
  daysLeft: number;
  expiresAt: string;
  onRenew: () => void;
  onDismiss?: () => void;
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export function SubscriptionExpiredModal({ daysLeft, expiresAt, onRenew, onDismiss }: Props) {
  const isExpired = daysLeft <= 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 max-w-sm w-full shadow-2xl">
        {isExpired ? (
          <>
            <div className="text-2xl mb-3">🔒</div>
            <h2 className="text-lg font-bold text-white mb-2">Premium истёк</h2>
            <p className="text-gray-400 text-sm mb-6">
              Ваш Premium закончился. Для продолжения работы продлите подписку.
            </p>
          </>
        ) : (
          <>
            <div className="text-2xl mb-3">⚠️</div>
            <h2 className="text-lg font-bold text-white mb-2">Подписка заканчивается</h2>
            <p className="text-gray-400 text-sm mb-6">
              Ваш Premium истекает через{" "}
              <span className="text-white font-semibold">{daysLeft} {pluralDays(daysLeft)}</span>{" "}
              ({formatDate(expiresAt)}). Продлите сейчас чтобы не потерять доступ к инструментам.
            </p>
          </>
        )}

        <button
          onClick={onRenew}
          className="w-full py-3 rounded-xl bg-gold text-black font-semibold hover:bg-gold-light transition-colors mb-3"
        >
          ⭐ Продлить за 750 Stars
        </button>

        {!isExpired && onDismiss && (
          <button
            onClick={onDismiss}
            className="w-full py-2 rounded-xl text-gray-400 hover:text-white text-sm transition-colors"
          >
            Позже
          </button>
        )}
      </div>
    </div>
  );
}

function pluralDays(n: number): string {
  if (n % 10 === 1 && n % 100 !== 11) return "день";
  if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) return "дня";
  return "дней";
}
