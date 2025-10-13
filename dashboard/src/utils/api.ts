export interface Player {
  id: number;
  name: string;
}

export interface RankHistoryEntry {
  club_id: number;
  match_id: number;
  /** YYYY-MM-DD */
  date: string;
  /** HH:MM:SS[.sss] */
  start_time: string;
  /** ISO 8601 date-time */
  datetime: string;
  winner: boolean;
  mu: number;
  sigma: number;
}

export interface RankHistory {
  player_id: number;
  history: RankHistoryEntry[];
}

export interface PlayerStats {
  player_id: number;
  averagePointsDifference: number;
  totalMatches: number;
  wins: number;
}

export interface OtherPlayerStatsEntry {
  partnerId: number;
  partnerName: number;
  wins: number;
  matches: number;
  winRate: number;
}

export interface PartnerStats {
  playerId: number;
  clubId: number;
  partners: OtherPlayerStatsEntry[];
}

export interface OpponentStats {
  playerId: number;
  clubId: number;
  opponents: OtherPlayerStatsEntry[];
}

export interface ValidationError {
  loc: Array<string | number>;
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export type FetchLike = typeof fetch;

/** Error thrown for non-2xx HTTP responses. */
export class ApiError<TBody = unknown> extends Error {
  public status: number;
  public url: string;
  public body?: TBody;

  constructor(
    message: string,
    opts: { status: number; url: string; body?: TBody }
  ) {
    super(message);
    this.name = "ApiError";
    this.status = opts.status;
    this.url = opts.url;
    this.body = opts.body;
  }
}

export interface SpiralOpenskillClientOptions {
  /** Base URL of the API, e.g. "http://localhost:8000" (no trailing slash) */
  baseUrl: string;
  /** Default headers to send on every request */
  headers?: Record<string, string>;
}

export class SpiralOpenskillClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor(opts: SpiralOpenskillClientOptions) {
    if (!opts?.baseUrl) {
      throw new Error("SpiralOpenskillClient: 'baseUrl' is required.");
    }
    this.baseUrl = opts.baseUrl.replace(/\/+$/, ""); // strip trailing slash
    this.defaultHeaders = {
      accept: "application/json",
      ...opts.headers,
    };
  }

  /** GET /players — Get People */
  async getPeople(signal?: AbortSignal): Promise<Player[]> {
    return this.request<Player[]>("/players", { method: "GET", signal });
  }

  /** GET /rank_history/{player_id} — Get Rank History */
  async getRankHistory(
    player_id: number,
    signal?: AbortSignal
  ): Promise<RankHistory> {
    if (!Number.isFinite(player_id)) {
      throw new Error("getRankHistory: 'player_id' must be a finite number.");
    }
    return this.request<RankHistory>(
      `/rank_history/${encodeURIComponent(String(player_id))}`,
      {
        method: "GET",
        signal,
      }
    );
  }

  async getPlayerStats(
    player_id: number,
    signal?: AbortSignal
  ): Promise<PlayerStats> {
    if (!Number.isFinite(player_id)) {
      throw new Error("getPlayerStats: 'player_id' must be a finite number.");
    }
    return this.request<PlayerStats>(
      `/player_stats/${encodeURIComponent(String(player_id))}`,
      {
        method: "GET",
        signal,
      }
    );
  }

  async getPartnerStats(
    player_id: number,
    club_id?: number,
    signal?: AbortSignal
  ): Promise<PartnerStats> {
    if (!Number.isFinite(player_id)) {
      throw new Error("getPlayerStats: 'player_id' must be a finite number.");
    }
    if (club_id === undefined) {
      return this.request<PartnerStats>(
        `/partner_stats/${encodeURIComponent(String(player_id))}`,
        {
          method: "GET",
          signal,
        }
      );
    }
    return this.request<PartnerStats>(
      `/partner_stats/${encodeURIComponent(
        String(player_id)
      )}?club_id=${encodeURIComponent(String(club_id))}`,
      {
        method: "GET",
        signal,
      }
    );
  }

  async getOpponentStats(
    player_id: number,
    club_id?: number,
    signal?: AbortSignal
  ): Promise<OpponentStats> {
    if (!Number.isFinite(player_id)) {
      throw new Error("getPlayerStats: 'player_id' must be a finite number.");
    }
    if (club_id === undefined) {
      return this.request<OpponentStats>(
        `/opponent_stats/${encodeURIComponent(String(player_id))}`,
        {
          method: "GET",
          signal,
        }
      );
    }
    return this.request<OpponentStats>(
      `/opponent_stats/${encodeURIComponent(
        String(player_id)
      )}?club_id=${encodeURIComponent(String(club_id))}`,
      {
        method: "GET",
        signal,
      }
    );
  }
  // ---- internals ----

  private async request<T>(
    path: string,
    init: RequestInit & { signal?: AbortSignal }
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      ...this.defaultHeaders,
      ...(init.headers ?? {}),
    };

    const res = await fetch(url, { ...init, headers });

    const isJson =
      res.headers
        .get("content-type")
        ?.toLowerCase()
        .includes("application/json") ?? false;

    let body: any = undefined;
    try {
      body = isJson ? await res.json() : await res.text();
    } catch {
      // ignore parse errors; body remains undefined
    }

    if (!res.ok) {
      // Special-case 422 to expose the spec'd HTTPValidationError shape
      if (res.status === 422) {
        throw new ApiError<HTTPValidationError>("Unprocessable Entity", {
          status: res.status,
          url,
          body,
        });
      }
      const message =
        typeof body === "object" &&
        body &&
        ("message" in body || "detail" in body)
          ? body.message ?? body.detail ?? `HTTP ${res.status}`
          : `HTTP ${res.status}`;
      throw new ApiError(message, { status: res.status, url, body });
    }

    return body as T;
  }
}

export const API_CLIENT = new SpiralOpenskillClient({
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
})
